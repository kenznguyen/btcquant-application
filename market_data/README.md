# T0 Canonical Market Data — SQLite-first

T0 is the independent market-data foundation for the Five-Layer System. The selected scope in this repository is Binance USD-M perpetual BTCUSDT candles at 15m and 1h, stored in SQLite and exposed through a bounded read-only Candle API.

See [T0 Active Scope Index](../docs/T0_ACTIVE_SCOPE_INDEX.md) for scope, exclusions and current readiness limits.

## Components

| Module | Responsibility |
|---|---|
| `store.py` | Candle contract, SQLite candle persistence and bounded reads |
| `storage.py` | Storage factory; SQLite is the selected default |
| `initialize_sqlite.py` | Explicit empty-only SQLite schema initializer |
| `feeder.py` | Lease, scheduler, recovery coordination, health and runtime contracts |
| `feeder_service.py` | Production composition/entrypoint (not currently runtime-verified) |
| `sync.py` | Bounded exchange candle synchronization |
| `write_gateway.py` | Single-writer, lease-fenced SQLite writes and WAL keeper |
| `api.py` | Authenticated read-only WSGI Candle API |

Public OHLCV acquisition uses CCXT's Binance USD-M adapter and does not require exchange API keys. The API is read-only; it does not call the exchange or expose write/order endpoints.

## Dependency contract

Direct dependencies are declared in `requirements-market-data.txt`:

- `ccxt==4.5.92`
- `gunicorn==23.0.0`

The committed `requirements-market-data.lock` pins the complete 25-package dependency set by exact version and SHA-256 wheel hash. Its verified compatibility target is **CPython 3.12 / Linux x86_64** only. Other Python versions and platforms are not certified by this lock.

The dependency compatibility workflow verifies hash-enforced wheel download and a separate offline fresh installation. See [dependency evidence](../docs/evidence/T0_DEPENDENCY_COMPATIBILITY_GATE_2026-11-19.md).

## SQLite initialization boundary

`initialize_sqlite.py` is an empty-only initializer. It refuses to overwrite an existing file/path, creates the expected `candles` and `feeder_leases` tables, checks SQLite integrity and verifies both tables are empty. Its CLI requires explicit `--confirm-create`.

The initializer has been tested only against disposable temporary paths in isolated CI. No canonical database has been created by this repository migration. Do not run the initializer against a real/canonical path without a separate explicit approval.

## Read-only Candle API contract

Endpoint: `GET /v1/candles`

Required query parameters:

- `symbol=BTCUSDT`
- `timeframe=15m|1h`
- `startMs`
- `endMs`

Optional: `asOfMs`.

Authentication: `Authorization: Bearer <MARKET_DATA_TOKEN>`. Never put tokens in URLs or logs.

Contract properties:

- UTC millisecond timestamps and half-open interval `[startMs,endMs)`.
- Bounded window, maximum 2,000 candles.
- Explicit market identity, timeframe, coverage and gaps.
- `datasetVersion` identifies the returned dataset/window content.
- First-observed availability is preserved; importing old candles later does not backdate their availability.
- A response with incomplete coverage is not a complete/evaluable window; consumers must inspect coverage and must not silently fill gaps.
- Missing storage/configuration fails closed; the API does not create a missing database.

## Verification

The current aggregate workflow is [T0 SQLite-only aggregate regression](https://github.com/kenznguyen/btcquant-application/actions/workflows/t0-sqlite-aggregate.yml).

Latest exact-SHA run: [44507725020](https://github.com/kenznguyen/btcquant-application/actions/runs/44507725020), SHA `42c8172a4b4b0234fa50e64eb6172f970f45ab66`, **191/191 PASS**.

The isolated tests use temporary SQLite databases, fake/synthetic exchange collaborators and no external network. PostgreSQL-specific tests are excluded. Passing CI does not prove real Binance connectivity, canonical historical-data availability, production feeder/API startup, systemd/VPS operation or production readiness.

## Explicit exclusions

- PostgreSQL/TimescaleDB adapters, migrations and qualification: PARKED.
- Kraken Spot: separate research domain, not canonical BTCUSDT Futures T0.
- Binance connectivity probe: manual diagnostic; not run by offline CI.
- Process/SIGKILL restart, systemd and VPS runtime: NOT VERIFIED / separately gated.
- T0→T2 end-to-end integration: separately gated.
- No canonical database or historical data payload is committed here.
- No automatic deletion, TTL, cleanup, archive, compaction, vacuum or backup expiry is authorized.
- No T1/T2 activation, paper/live execution or real orders are authorized by these tests.

T0 remains an independent data asset. Production readiness is **NOT CERTIFIED**.
