# T0 Canonical Market Data — SQLite-first

T0 is the independent market-data foundation for the Five-Layer System. The selected scope in this repository is Binance USD-M perpetual BTCUSDT candles at 15m and 1h, stored in SQLite and exposed through a bounded read-only FastAPI Candle API.

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
| `fastapi_app.py` | Authenticated read-only FastAPI ASGI Candle API |

Public OHLCV acquisition uses CCXT's Binance USD-M adapter and does not require exchange API keys. The API is read-only; it does not call the exchange or expose write/order endpoints. FastAPI is the sole HTTP adapter; the legacy WSGI/Gunicorn serving path has been retired.

## Dependency contract

Direct dependencies are declared in `requirements-market-data.txt`:

- `ccxt==4.5.92`

The committed `requirements-market-data.lock` pins the CCXT ingestion dependency closure by exact version and SHA-256 wheel hash. FastAPI/Uvicorn serving dependencies are pinned separately in `requirements-market-data-fastapi.lock`. Its verified compatibility target is **CPython 3.12 / Linux x86_64** only. Other Python versions and platforms are not certified by this lock.

The dependency compatibility workflow verifies hash-enforced CCXT wheel download and a separate offline fresh installation. The dedicated FastAPI workflow independently verifies the ASGI runtime lock. See [dependency evidence](../docs/evidence/T0_DEPENDENCY_COMPATIBILITY_GATE_2026-11-19.md).

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
- `generatedAtMs` records response generation time. Freshness evaluation uses `asOfMs` when supplied (`evaluationAnchor=AS_OF`), otherwise `generatedAtMs` (`GENERATED_AT`). Future `asOfMs` values are rejected.
- `timestampValid` requires every returned candle to have nonnegative integer timestamps, timeframe-aligned opens, an exclusive close equal to open plus one interval, first observation no earlier than close, no future availability relative to the evaluation time, and a contiguous open-time grid (each candle exactly one interval after its predecessor). Duplicates, out-of-order rows and gaps invalidate the timestamp sequence even if a caller incorrectly claims complete coverage.
- `fresh` is true only when the latest returned candle is exactly the latest closed candle expected at the evaluation time; its close lag must be within `[0, one timeframe)`.
- `evaluable` is true only when coverage is complete, timestamps are valid and the latest candle is fresh. Empty, stale, timestamp-invalid or incomplete windows are not evaluable.
- Contract version is `1.1.0`; schema version remains 1 because the new freshness fields are additive.
- The FastAPI T0 endpoint and the Application Common API `/v1/candles` adapter use the same `candle_envelope()` builder for contract version, schema, provenance, generated/as-of anchor and freshness fields. Both map malformed/duplicate queries and future `asOfMs` to `400 INVALID_QUERY`; storage failures remain fail-closed.
- Missing storage/configuration fails closed; the API does not create a missing database.

## Verification

The current regression gates are:
- [T0 FastAPI contract regression](https://github.com/kenznguyen/btcquant-application/actions/workflows/t0-fastapi-migration.yml)
- [T0 SQLite-only aggregate regression](https://github.com/kenznguyen/btcquant-application/actions/workflows/t0-sqlite-aggregate.yml)
- [T0 dependency compatibility](https://github.com/kenznguyen/btcquant-application/actions/workflows/t0-dependency-compatibility.yml)

Post-retirement verification:
- FastAPI, migrated API/ingestion acceptance and retirement guards: [run 44546084887](https://github.com/kenznguyen/btcquant-application/actions/runs/44546084887), exact SHA `c77ab92b621b2e79167d6b8eb910be015b428f62`, **50/50 PASS**.
- Runtime-lock-only install, ASGI import and in-process health: same run, **PASS**; no socket was opened.
- SQLite aggregate: [run 44546084972](https://github.com/kenznguyen/btcquant-application/actions/runs/44546084972), same exact SHA, **174/174 PASS**.
- F1 write-gateway regression: [run 44546084937](https://github.com/kenznguyen/btcquant-application/actions/runs/44546084937), same exact SHA, **14/14 PASS**.
- Dependency compatibility after removing Gunicorn: [run 44545799691](https://github.com/kenznguyen/btcquant-application/actions/runs/44545799691), exact dependency-change SHA `7bc8fab6b6c6f49ed70b7370a113958d7981cd20`, **PASS**.

Detailed evidence, job IDs and artifact SHA-256 digests: [T0 WSGI/Gunicorn retirement report](../docs/evidence/T0_WSGI_GUNICORN_RETIREMENT_2026-11-19.md).

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
