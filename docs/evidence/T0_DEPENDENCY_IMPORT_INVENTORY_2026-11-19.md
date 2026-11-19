# T0 Migration Dependency and Import Inventory

Date: 2026-11-19
Target branch: `main`
Snapshot commit under review: `fcaa2efefdd4b3e481e9db951d538824596d0038`
Source: `kenznguyen/btcusdt-telegram-signals2`, branch `feature/t0-centralized-data-feeder-p1-20261101`, source documentation/evidence HEAD `8623d1076d6b821091ff9da0d84033f48fd8ba7a`.

## Scope

Read-only inspection of the migrated T0 modules, copied tests, source dependency manifest, and selected T0 support paths. No code, dependency manifest, workflow, runtime, database, or source repository was changed. No tests or workflows were run.

## Findings

### 1. Python import structure

- The copied modules use standard-library imports plus package-relative absolute imports such as `from market_data.store import ...`.
- `market_data/__init__.py` is absent in the source branch at the inspected ref and was not copied. Python namespace-package imports can work without it on supported Python versions, but packaging/install behavior has not been verified.
- Internal import links among the copied modules are present for the inspected paths:
  - `feeder.py` → `store.py`
  - `storage.py` → `store.py`, `postgres.py`
  - `api.py` → `store.py`, `postgres.py`, `storage.py`
  - `sync.py` → `store.py`, `write_gateway.py`
  - `feeder_service.py` → `feeder.py`, `storage.py`, `postgres.py`, `sync.py`, `store.py`, `write_gateway.py`
  - `migrations.py` → `postgres.py`

### 2. Dependency manifest gap

- Source `requirements.txt` blob: `f5c242bdac51eba200b19233e08e7d4b22f598c4`. It was not copied.
- That manifest lists `requests`, `numpy`, `pandas`, `Flask`, `gunicorn`, `cryptography`, and `rfc8785`; it does not list `ccxt` or `psycopg`.
- T0 Feeder's exchange path lazily imports `ccxt`; the PostgreSQL path lazily imports `psycopg`. Gunicorn is relevant to the documented API serving approach. Exact pinned/compatible versions and the minimum supported Python version are NOT VERIFIED.
- Do not install packages or add a guessed requirements file based on this inventory.

### 3. Missing source assets / tests

- `market_data/migrations.py` reads SQL files from sibling directory `market_data/migrations/` using pattern `[0-9][0-9][0-9]_*.sql`. That directory was not copied, so the PostgreSQL migration runner has no migration payload in this snapshot.
- Source file `market_data/migrations/002_t0_feeder_leases.sql` exists at blob `009474f187a143381e5b29209a64709698795854`; it is not in the target snapshot. Other expected migration names were not established in this inspection.
- Source tests `market_data/test_sync.py` (blob `319e084d9c0a9c5b0319e9bb7d1f93a930564dc8`) and `market_data/test_api.py` (blob `49df7e0bec12908adae67f18a4aa19063e461093`) exist but were not copied.
- Source `market_data/test_timescaledb.py` (blob `59f8ca223b1cd7e580afed18e0be0d0fb0e72ea4`) requires a dedicated disposable local TimescaleDB test target and was not copied.
- The target currently has only four focused T0 tests: feeder recovery, feeder lease, write gateway, and storage. This is not full T0 regression coverage.

## Status

- Static import-link inspection: PARTIAL PASS for the selected modules.
- Dependency closure: BLOCKED / NOT VERIFIED.
- PostgreSQL migration completeness: BLOCKED (SQL migration directory absent).
- Test coverage parity: PARTIAL; two relevant SQLite/API test modules and the TimescaleDB test are not included.
- Test execution: NOT RUN.
- Runtime / database / canonical data: NOT VERIFIED / NOT COPIED.
- Production readiness: NOT CERTIFIED.

## Recommended next gate

Before running tests, perform a bounded source-to-target reconciliation of the missing T0 files and classify each as required for SQLite-only baseline, optional PostgreSQL, or out-of-scope. Keep the public repository free of credentials and canonical data. Do not install dependencies, copy PostgreSQL migrations, run tests, or dispatch workflows until that file/dependency scope is explicitly approved.
