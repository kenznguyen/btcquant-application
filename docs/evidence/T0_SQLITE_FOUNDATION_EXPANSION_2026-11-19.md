# T0 SQLite foundation expansion — 2026-11-19

## Scope

This increment extends the new repository's SQLite-first T0 foundation with selected source modules and offline contract tests. The source repository is read-only.

- Target: `kenznguyen/btcquant-application`, branch `main`.
- Source: `kenznguyen/btcusdt-telegram-signals2`, branch `feature/t0-centralized-data-feeder-p1-20261101`.
- Exact source HEAD inspected: `c0f48b8910655fdb40d14214ad048b1d3cfa7fe9`.
- No canonical SQLite database or market-data payload was copied or created.

## Files migrated

All nine files below are byte-identical to the inspected source blobs:

| Target path | Source/target blob | Tests |
|---|---|---:|
| `market_data/initialize_sqlite.py` | `58bd2deba66cc667bad8d6446c5ff54e7f5dd240` | implementation |
| `market_data/test_initialize_sqlite.py` | `9823f42fa1b346c7c5b96786eec7e996484b692d` | 4 |
| `market_data/test_store.py` | `df1554a365ff5d619498dc4b07f7a1a435e761df` | 13 |
| `market_data/test_fenced_store.py` | `0573d0728f3e62a95b8d2a4f16359e33dd4789b4` | 2 |
| `market_data/test_feeder_health.py` | `80e0b7d042c821d4814d626b69c3196853dc49d9` | 12 |
| `market_data/test_feeder_retry.py` | `0c556f2954188e2bf3bd643aa217f71b9bd8ba2c` | 12 |
| `market_data/test_feeder_scheduler.py` | `695c53548c58763cffecc86626171f6a691e75fd` | 20 |
| `market_data/test_controlled_ingestion_acceptance.py` | `92c76fea839858f128ed228ac25b36b6bb8ec375` | 4 |
| `market_data/test_t0_controlled_ingestion_acceptance.py` | `a26d9f44012452fa663553e292e273d68d625e88` | 1 |

Total new test coverage: **68** tests. The initializer is an explicit empty-only creator: it refuses an existing file/path, creates only a new empty schema, checks integrity and zero rows, and requires `--confirm-create` for CLI use. In this CI increment the initializer function was exercised only against disposable temporary paths by its tests; the CLI was not run against any canonical path.

## Aggregate SQLite-only workflow update

- Workflow: `.github/workflows/t0-sqlite-aggregate.yml`.
- Update commit / exact tested source SHA: `42c8172a4b4b0234fa50e64eb6172f970f45ab66`.
- Workflow blob: `32be957fbad1b04161b621c7e1c95f20aa9d9cf9`.
- Extended explicit allowlist from 123 to **191** tests, adding initializer, CandleStore, fenced-write concurrency, health, retry, scheduler and synthetic controlled-ingestion contracts.
- Still excludes PostgreSQL-specific API/Storage tests and all PostgreSQL/TimescaleDB modules.

## Authoritative verification

- GitHub Actions run [44507725020](https://github.com/kenznguyen/btcquant-application/actions/runs/44507725020).
- Job: `135503600404`.
- Exact checkout SHA: `42c8172a4b4b0234fa50e64eb6172f970f45ab66`.
- Result: **SUCCESS**, `Ran 191 tests in 3.131s`, `OK`, 0 failures, 0 errors.
- Artifact: `t0-sqlite-aggregate-evidence`, ID `14520188043`, size 6,093 bytes, SHA-256 `0389c4fc4cab0190ea7ada4115b24b53095a9ffb035cba3f7b1dcd01b22ceacb`, expires 2026-12-03T10:40:03Z.
- Artifact ZIP downloaded and independently hashed. Payload inspection confirmed exact checkout SHA, 191 tests, exit code 0, pinned Python image ID and scope/isolation metadata.
- Container: Python 3.12.16 immutable image; Docker `--network none`, read-only source/root, non-root, dropped capabilities, no-new-privileges, no credentials, no canonical DB mount. Tests use temporary SQLite, fakes and synthetic exchange responses only.

## Remaining source-only items and exclusions

The source directory contains additional assets not migrated in this increment. They are deliberately not treated as missing implementation until separately classified:

- `market_data/README.md` — documentation not yet reconciled with target documentation/index structure.
- `test_feeder_health_api.py` — imports legacy top-level `app`, which is not part of the selected target T0 API surface.
- `test_feeder_process_restart.py` — process/SIGKILL-level restart test; production-process lifecycle scope remains separately gated.
- `test_e2e_data_flow.py` and `test_t0_t2_parity.py` — include T2 consumer/integration scope.
- `binance_connectivity_probe.py` and its tests — explicit external connectivity probe; not included in offline SQLite gate.
- `migrations/`, PostgreSQL and TimescaleDB tests/assets — PostgreSQL/TimescaleDB remains excluded.
- Kraken-specific modules/tests — outside BTCUSDT Binance USD-M T0 scope.
- `test_single_writer_gateway_red.py` — legacy static RED contract spec not included in this aggregate gate.

## Status

- **PASS** — nine selected SQLite foundation files migrated with exact source/target blob parity.
- **PASS** — 68 additional source test methods preserved.
- **PASS** — expanded exact-SHA aggregate SQLite gate 191/191.
- **PASS** — artifact checksum and payload verification.
- **NOT VERIFIED / NOT AUTHORIZED** — current canonical data/OOS bundle, production feeder/API startup, process restart, systemd/VPS runtime, real Binance connectivity, PostgreSQL/TimescaleDB, T1/T2 integration and production readiness.

No source repository changes, canonical DB/data, production runtime, VPS, deployment, T1/T2 or trading behavior occurred. No live orders.
