# T0 Missing-File Reconciliation

Date: 2026-11-19 (Asia/Ho_Chi_Minh)
Target repository: `kenznguyen/btcquant-application`
Target branch: `main`
Snapshot baseline: `fcaa2efefdd4b3e481e9db951d538824596d0038`
Source repository: `kenznguyen/btcusdt-telegram-signals2`
Source branch: `feature/t0-centralized-data-feeder-p1-20261101`
Source code baseline: `eb91528bab2b994f283dbe34cd7b0bcbfe406cb5`
Source documentation/evidence HEAD: `8623d1076d6b821091ff9da0d84033f48fd8ba7a`

## Approval and scope

Owner approved the read-only Missing-File Reconciliation and subsequently approved recording this result in a new evidence report and updating the target session handoff.

This increment records the reconciliation only. It does not copy missing source files, install or modify dependencies, execute tests, dispatch workflows, change source code, mutate databases/canonical data, inspect or operate runtime infrastructure, or alter the source repository.

The source file SHAs below were re-fetched from the named source branch during this recording step. They are Git blob SHAs, not commit SHAs.

## 1. Missing-file classification

### SQLite / API baseline candidates

| Source path | Source blob SHA | Size (bytes) | Classification | Disposition |
|---|---|---:|---|---|
| `market_data/test_sync.py` | `319e084d9c0a9c5b0319e9bb7d1f93a930564dc8` | 8,379 | SQLite sync regression candidate | Recommend adding only after a separate copy approval and compatibility review |
| `market_data/test_api.py` | `49df7e0bec12908adae67f18a4aa19063e461093` | 10,780 | SQLite/API regression candidate; includes some PostgreSQL fail-closed coverage | Recommend adding only after a separate copy approval and compatibility review |

These tests are relevant to the SQLite/API baseline but their presence alone does not establish that they pass against the selected snapshot. No test was run.

### Optional PostgreSQL / TimescaleDB assets

| Source path | Source blob SHA | Size (bytes) | Classification | Disposition |
|---|---|---:|---|---|
| `market_data/migrations/001_initial_timescale.sql` | `777d884d217004569e97821a76b506572ee8f5b7` | 2,197 | PostgreSQL/TimescaleDB migration | Not required for SQLite-only baseline |
| `market_data/migrations/002_t0_feeder_leases.sql` | `009474f187a143381e5b29209a64709698795854` | 506 | PostgreSQL/TimescaleDB migration | Not required for SQLite-only baseline |
| `market_data/migrations/003_t0_database_fenced_candle_writer.sql` | `1e08f77a9e6411050f370f8f14096dcbff605aea` | 9,288 | PostgreSQL/TimescaleDB migration | Not required for SQLite-only baseline |
| `market_data/migrations/004_t0_fenced_lease_api.sql` | `cc79631a0c4e12010dc120413973cab7f84f6406` | 11,520 | PostgreSQL/TimescaleDB migration | Not required for SQLite-only baseline |
| `market_data/test_timescaledb.py` | `59f8ca223b1cd7e580afed18e0be0d0fb0e72ea4` | 10,514 | TimescaleDB integration test | Requires a separately isolated disposable TimescaleDB test service |

The four SQL files above are the complete numbered migration set found under the source branch's `market_data/migrations/` directory during this reconciliation. The target's migration runner expects sibling SQL migration assets, so PostgreSQL migration execution is incomplete in the current snapshot. This does not block SQLite-only use by itself; PostgreSQL remains optional and not enabled/certified.

### Out-of-scope

- No other missing file was approved for transfer in this increment.
- No workflow, environment file, credential, database, canonical market-data payload, runtime configuration, or deployment asset is authorized for copying.
- No `market_data/__init__.py` was found at the inspected source baseline; do not synthesize one without evidence of a packaging requirement.

## 2. Dependency reconciliation

Source `requirements.txt` blob SHA: `f5c242bdac51eba200b19233e08e7d4b22f598c4`. It lists `requests`, `numpy`, `pandas`, `Flask`, `gunicorn`, `cryptography`, and `rfc8785`. It was not copied.

The manifest does not list `ccxt` or `psycopg`, although the Feeder exchange path lazily imports `ccxt` and the optional PostgreSQL path lazily imports `psycopg`. `gunicorn` is relevant to the documented API serving path. Exact compatible versions, transitive dependency closure, and minimum supported Python version remain NOT VERIFIED.

Do not copy the repository-wide requirements manifest, install packages, or create a guessed dependency manifest on the basis of this inventory alone. A separate dependency-resolution and compatibility gate is required before test execution.

## 3. Structural observations

- `market_data/__init__.py` is absent at the inspected source baseline; no file was omitted from the snapshot on this account.
- The target snapshot has four focused T0 tests (feeder recovery, feeder lease, write gateway, and storage). It does not have full source test parity.
- `test_timescaledb.py` requires a dedicated disposable TimescaleDB target. It must not be run against canonical or shared data.
- No legacy workflow was identified as necessary to record or reconcile these missing files. Workflow migration remains outside this scope.

## 4. Status

| Control | Status | Basis |
|---|---|---|
| Source-to-target file inventory | PASS | Missing paths and exact source blob SHAs re-fetched |
| SQLite / PostgreSQL classification | PASS | Classified by test/backend role and migration path |
| Missing-file SHA identification | PASS | Exact blob SHAs recorded above |
| Dependency closure | NOT VERIFIED | No dependency resolution/install or compatibility test |
| SQLite test parity | PARTIAL | Two relevant test modules absent from target |
| PostgreSQL migration completeness in target | BLOCKED | Four SQL migrations are absent |
| Test execution | NOT RUN | Explicitly outside approved scope |
| Workflow execution | NOT RUN | Explicitly outside approved scope |
| Runtime / canonical database | NOT VERIFIED | No runtime or database access |
| Production readiness | NOT CERTIFIED | No tests/runtime/data certification |

## 5. Next gate

Recommended next step: request separate approval to add only `market_data/test_sync.py` and `market_data/test_api.py` to the existing target `main`, after reviewing their imports and test isolation requirements. This is a proposed scope, not authorization to copy or execute them.

Keep PostgreSQL migrations and `test_timescaledb.py` excluded until PostgreSQL/TimescaleDB is explicitly selected and a disposable test service and migration plan are approved. Resolve dependency versions and Python compatibility before running any tests.

## 6. Change record and limits

- Evidence report creation: documentation-only.
- Session handoff update: documentation-only.
- Source repo: unchanged.
- Application source/tests/dependencies/workflows: unchanged.
- Canonical data/database/runtime/VPS/deployment: untouched.
- Tests and workflows: NOT RUN.
- No merge, rebase, cherry-pick, reset, force-push, or branch creation.


## 7. Approved SQLite/API test-file transfer (2026-11-19)

Owner separately approved copying only the two SQLite/API regression test modules listed below. Source contents were fetched from the source branch named in this report and added unchanged to target `main`.

| Path | Source blob SHA | Target commit |
|---|---|---|
| `market_data/test_sync.py` | `319e084d9c0a9c5b0319e9bb7d1f93a930564dc8` | `3aa983c1d71e8fa054ffc61dcea2ec889d504b48` |
| `market_data/test_api.py` | `49df7e0bec12908adae67f18a4aa19063e461093` | `7f5cf81eebdc53aae76adbba98c980219aefa15a` |

Static isolation review before transfer:
- Both tests create temporary directories/databases and register cleanup.
- The sync test uses a mocked exchange object; its subprocess checks module help and verifies the manual CLI rejects a request lacking `--shadow-only` before exchange access.
- The API test invokes the WSGI application directly, patches environment variables, and uses temporary SQLite paths. Its PostgreSQL case verifies fail-closed behavior without a DSN; it does not connect to PostgreSQL.
- No canonical database path, network exchange connection, shared database, live order, or runtime service is invoked by the reviewed test code.

Transfer result: source text copied unchanged. Target blob equality and test behavior remain subject to readback verification and later test execution respectively. No tests were run in this transfer increment.
