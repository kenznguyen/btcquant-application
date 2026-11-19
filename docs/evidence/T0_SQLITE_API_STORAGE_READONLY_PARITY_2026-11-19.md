# T0 SQLite Read-only API and Storage Parity Inventory — 2026-11-19

Target repository: `kenznguyen/btcquant-application`
Target branch: `main`
Target HEAD inspected: `c80aa8e31481d237cb8d17ab547d65e7e790976a`
Source repository: `kenznguyen/btcusdt-telegram-signals2`
Source branch: `feature/t0-centralized-data-feeder-p1-20261101`
Source HEAD inspected: `c0f48b8910655fdb40d14214ad048b1d3cfa7fe9`

## Scope

Read-only comparison of the T0 canonical SQLite HTTP read API and Storage factory/adapter between source and target after legacy CI trigger isolation.

No code, tests, workflow, dependency manifest or data was changed in this inventory. No test command or workflow was run.

## Direct API and Storage parity

| File | Source blob | Target blob | Result |
|---|---|---|---|
| `market_data/api.py` | `81733c9b6de811cbebb2f5d472d41f37f337990c` | same | BYTE-IDENTICAL |
| `market_data/storage.py` | `13fe1ae01ebb5318b69e69eef3e512d207f74c49` | same | BYTE-IDENTICAL |
| `market_data/test_api.py` | `49df7e0bec12908adae67f18a4aa19063e461093` | same | BYTE-IDENTICAL |
| `market_data/test_storage.py` | `b2635f575323187f936360d033b4fc630d8138e0` | same | BYTE-IDENTICAL |

Static contract observations from the identical files:
- API is WSGI read-only: GET only; `/health` and `/v1/candles`; no order endpoint.
- `/v1/candles` requires configured bearer token and configured SQLite DB path; token comparison uses `hmac.compare_digest`; missing configuration and store errors fail closed.
- Query validation is bounded: BTCUSDT only, supported timeframe only, one value per parameter, ASCII nonnegative integer timestamps, aligned nonempty half-open window, maximum 2,000 candles, optional `asOfMs`.
- Response includes contract/schema version, market identity, volume unit, source, dataset version and freshness metadata. JSON disallows NaN; responses set `Cache-Control: no-store`.
- Storage defaults to SQLite. SQLite constructor is side-effect-free; explicit `initialize()` creates the writer/schema, while `read_window()` reads without creating a missing database.
- Backend selection is explicit; unknown backend and PostgreSQL-without-DSN fail closed rather than falling back to SQLite. No implicit migration is performed by the storage facade.
- API test file contains 13 test methods; Storage test file contains 7. These are test specifications only; none were executed in this inventory.

## Dependency parity

| Dependency | Source blob | Target blob | Result |
|---|---|---|---|
| `market_data/store.py` | `4e1b0c54bd56455abe5be0e5c7d0807e63e0bc78` | same | BYTE-IDENTICAL |
| `market_data/feeder.py` | `299a9b5a8b1ebd581eb620d5ee860d9f9ff5dc5c` | same | BYTE-IDENTICAL |
| `market_data/sync.py` | `e7ad4e6f2074225957b01f74abb0befe37675ea2` | same | BYTE-IDENTICAL |
| `market_data/postgres.py` | `2fe27fe2d066dda0c192a381b72d27404487b800` | same | BYTE-IDENTICAL (static identity only; no PostgreSQL validation performed) |
| `market_data/write_gateway.py` | `585caf5250c7382f8e391533882f08c8ec97efaa` | `0a77df443ae1a817ea74946fac5dc0f3809ddd83` | BYTE-DIFFERENT |

The only byte divergence found in the inspected API/Storage dependency set is `write_gateway.py`. The source uses a `columns("feeder_leases")` helper for schema inspection; the target performs the equivalent direct `PRAGMA table_info(feeder_leases)` inspection. Both check the exact ordered columns and primary key. The target F1 malformed-schema regression and its isolated 14-test write-gateway run were already recorded in the F1 evidence; this inventory does not rerun them or broaden that evidence.

The API and Storage test modules use the target write gateway in temporary test fixtures. Their test files are byte-identical to source, while the gateway dependency differs in implementation shape as noted above.

## CI isolation status

The legacy `.github/workflows/t0-sqlite-api-isolated.yml` is now `workflow_dispatch` only and checks out `${{ github.sha }}`, with a preflight equality check against `GITHUB_SHA`. Its seven-module suite still contains feeder lifecycle tests, but a push to `main` no longer triggers it. No workflow was dispatched for this read-only inventory.

CI isolation implementation commit: `91f89424da0e8c00ca56397b72364dab678eb32d`.
Isolation evidence commit: `6f323b3652e00f38b9edd8e4c4f685cc32fc9ccf`.

## Status

- Direct API implementation parity: PASS (byte-identical).
- Storage factory/adapter parity: PASS (byte-identical).
- API/Storage test specification parity: PASS (byte-identical; 13 + 7 methods).
- Inspected shared dependencies: PASS for `store.py`, `feeder.py`, `sync.py`; `postgres.py` byte-identical only, no PostgreSQL behavior evaluated.
- Write gateway byte parity: DIVERGED; F1 schema-guard behavior was separately verified in prior evidence.
- API/Storage runtime tests: NOT RUN / NOT VERIFIED.
- Full T0 parity, lifecycle, recovery, canonical data and operational readiness: NOT CERTIFIED.

## Strict non-changes

No source repository change. No application code/test change. No PostgreSQL execution or migration. No canonical database/data, VPS, runtime, T1/T2, paper/live trading, exchange or execution access. No dependency installation. No workflow dispatch. No branch creation, merge, rebase, cherry-pick, reset or force-push.

## Next bounded step

If separately approved, create a dedicated SQLite-only API/Storage regression gate that runs only `market_data.test_api` and the SQLite-only subset of `market_data.test_storage`, excluding PostgreSQL-specific cases and all feeder lifecycle modules. Keep it exact-SHA, pinned Python, network-isolated, read-only source, no credentials and no canonical DB mount. Do not invoke the manual legacy seven-module workflow for routine API/Storage checks.
