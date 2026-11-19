# T0 WSGI/Gunicorn Retirement — Implementation and Verification — 2026-11-19

## 1. Owner decision and review disposition

- Owner approval: **APPROVED** in `docs/decisions/T0_WSGI_GUNICORN_RETIREMENT_APPROVAL_2026-11-19.md`.
- Human independent second-person review: **WAIVED BY OWNER** for this bounded retirement.
- Gemini external AI review: **BLOCKED / NOT VERIFIED** because Gemini could not access the repository or exact SHA. No Gemini source-level approval is claimed.
- ChatGPT supplementary review: completed, but non-independent; no confirmed blocking defect was identified within the bounded static scope.
- No human engineering sign-off or formal compliance certification is claimed.

## 2. Repository and exact source identity

- Repository: `kenznguyen/btcquant-application`.
- Branch: `main`.
- Owner-approval baseline HEAD: `7fdf4e3eedaf0b568c7219ee8b140684ff066718`.
- Retirement implementation commit: `7bc8fab6b6c6f49ed70b7370a113958d7981cd20`.
- Test-fix / exact tested source SHA: `c77ab92b621b2e79167d6b8eb910be015b428f62`.
- Current main after manual-workflow cleanup: `d6c25716e07b9c8414e34bde11d31a6a62d33f43`.
- Compare `c77ab92...` to current main `d6c257...`: **1 ahead / 0 behind**; the only changed file is `.github/workflows/t0-sqlite-api-isolated.yml`, which is manual-only and no longer runs API tests. No application source, test code, runtime dependency or canonical data drift after the tested SHA.

## 3. Changes completed

### WSGI and Gunicorn removal

- Deleted `market_data/api.py`, including the WSGI callable and local WSGI server entrypoint.
- Deleted `market_data/test_fastapi_parity.py` after preserving the completed C1 ten-case differential evidence in the prior review/evidence records.
- Removed `gunicorn==23.0.0` from `requirements-market-data.txt` and its committed `requirements-market-data.lock`.
- Updated dependency compatibility CI to verify CCXT 4.5.92 only; no Gunicorn import or command remains in that dependency gate.
- Updated `market_data/README.md` to identify `fastapi_app.py` as the sole T0 HTTP adapter and describe the separate FastAPI runtime lock.

### Test migration

- Migrated all 18 tests in `market_data/test_api.py` to `fastapi.testclient.TestClient` and `market_data.fastapi_app.app`; deterministic clock patches now target the FastAPI adapter.
- Migrated API calls in `market_data/test_controlled_ingestion_acceptance.py` and `market_data/test_t0_controlled_ingestion_acceptance.py` to ASGI requests. Synthetic exchange and temporary SQLite isolation remain.
- Updated `market_data/test_write_gateway.py`'s standard-library-only SQLite dependency-closure test so it imports core feeder/storage modules, not the retired HTTP adapter. FastAPI runtime dependencies are separately locked and tested.
- Added `market_data/test_wsgi_retirement.py` with guards that prove the old `market_data.api` module is not importable and Gunicorn is absent from both T0 runtime manifest and lock.

### CI and workflow cleanup

- FastAPI workflow now runs the ASGI contract suite, all migrated API/ingestion acceptance tests and retirement guards; expected count is 50.
- SQLite aggregate workflow no longer requires the WSGI module or runs API/acceptance modules; expected count is 174. Those HTTP/acceptance tests run in the FastAPI workflow.
- Removed obsolete push-triggered `t0-sqlite-api-storage.yml`, whose required WSGI file check became invalid.
- Updated the manual `t0-sqlite-api-isolated.yml` workflow to retain its six SQLite/storage/feeder modules while excluding the API test module, now covered by the FastAPI workflow.
- T0 F1 regression workflow remains active and verifies write-gateway regressions.

## 4. TDD and CI evidence

### RED — expected retirement guards failed before removal

- Test-only guard commit: `3f836ab900b132d01c08f0c720af96aa4eb21d10`.
- RED workflow/path commit: `dd74189174d4be5311e78402416f176f62a39e1e`.
- FastAPI workflow [44545128476](https://github.com/kenznguyen/btcquant-application/actions/runs/44545128476), job `135633537880`: failed as expected because the legacy WSGI module and Gunicorn were still present. The two new retirement assertions both failed. The pre-existing FastAPI contract tests and runtime-lock smoke passed.
- SQLite aggregate workflow [44545128538](https://github.com/kenznguyen/btcquant-application/actions/runs/44545128538): success on the RED commit.

### GREEN — exact tested source SHA

All final contract/regression runs below checked out exact source SHA:

`c77ab92b621b2e79167d6b8eb910be015b428f62`

| Verification | Workflow / job | Result | Artifact | Artifact SHA-256 |
|---|---|---:|---:|---|
| FastAPI + migrated API/ingestion + retirement guards | [44546084887](https://github.com/kenznguyen/btcquant-application/actions/runs/44546084887), job `135636899975` | **50/50 PASS** | `14540552439` | `f980857c9a8fb823f07f7b6803388d7960d63eac33d734f357e82583647de320` |
| Runtime-lock install, ASGI import and in-process health | [44546084887](https://github.com/kenznguyen/btcquant-application/actions/runs/44546084887), job `135636899187` | **PASS** | `14539872493` | `87cecaa722f5ffde1fce8d6b73af735900076040bddcd6f76052bfb89a37d58e` |
| SQLite-only aggregate | [44546084972](https://github.com/kenznguyen/btcquant-application/actions/runs/44546084972), job `135636899559` | **174/174 PASS** | `14539742479` | `943fb0987ff2f9493478427e87750da5bc9e18354a5cc13c73cab0e976605b67` |
| F1 write-gateway regression | [44546084937](https://github.com/kenznguyen/btcquant-application/actions/runs/44546084937), job `135636899426` | **14/14 PASS** | `14540692122` | `057c01a69b30ad814cdf1a84178b054d3b50cb7058de55e4fb20afce061ed30e` |

The FastAPI runtime smoke confirmed:
- `pip check`: no broken requirements.
- `runtime_lock_install=PASS`.
- `asgi_import=PASS`.
- `in_process_health=PASS`.
- No socket, canonical SQLite, credentials, exchange or external service was used.

### Dependency compatibility after Gunicorn removal

- Exact source SHA containing the dependency-manifest/lock removal: `7bc8fab6b6c6f49ed70b7370a113958d7981cd20`.
- Workflow [44545799691](https://github.com/kenznguyen/btcquant-application/actions/runs/44545799691), job `135635880436`: **SUCCESS**.
- Artifact `14540027219`; SHA-256 `f6b7c6bfaf69070ba5256e4c80beef475c783eaadd831ecda7ce3e6c27fad80a`.
- Fresh CPython 3.12.16 offline install from the committed lock passed; `pip check` reported no broken requirements; CCXT 4.5.92 and the Binance USD-M adapter were verified.
- The dependency files were unchanged between `7bc8fab...` and the final tested source SHA `c77ab92...`.

## 5. Iteration failures and closure

The first post-removal CI iteration exposed two migrated-test mistakes (a missing `json` import and response-object/dictionary confusion), plus a core dependency-closure test still importing the deleted WSGI module. The obsolete push-triggered API/Storage workflow also still required `market_data/api.py`.

These were corrected:
- Restored the JSON import needed by the migrated API test.
- Asserted against the decoded ASGI response payload.
- Removed the WSGI import from the core standard-library-only dependency-closure test.
- Removed the obsolete WSGI-only API/Storage workflow and adjusted the manual suite.

The corrected exact-SHA runs above passed. Intermediate failed runs are iteration evidence, not acceptance evidence.

## 6. Contract preservation and boundaries

Preserved by the migrated tests and current FastAPI adapter:
- Candle Contract 1.1.0 and schema version.
- `GET /health` and authenticated `GET /v1/candles`.
- Bearer authentication and fail-closed configuration/storage behavior.
- Status/error semantics, bounded query behavior, freshness/evaluability and `asOfMs`.
- Decimal OHLCV serialization, coverage/gaps and provenance.
- `Cache-Control: no-store` and read-only storage behavior.

No changes were made to canonical T0 SQLite ownership or contents, writer fencing, lease, feeder, scheduler, recovery, schema, ingestion semantics, T1/T2, PostgreSQL, data retention/deletion or trading.

## 7. Final status and remaining gates

- WSGI source retirement: **PASS**.
- Gunicorn dependency retirement: **PASS**.
- Migrated FastAPI/API/ingestion tests: **50/50 PASS**.
- SQLite aggregate: **174/174 PASS**.
- F1 write-gateway regression: **14/14 PASS**.
- Dependency compatibility after Gunicorn removal: **PASS**.
- Owner approval: **APPROVED**; human independent review prerequisite **WAIVED BY OWNER**.
- Gemini review: **BLOCKED / NOT VERIFIED**; no external-model code-level approval claimed.
- Uvicorn process/socket startup, endpoint probe, Nginx, VPS/systemd/autostart, runtime activation and deployment: **NOT VERIFIED / NOT AUTHORIZED**.
- Production readiness: **NOT CERTIFIED**.

Next step requires a separate owner approval for any Uvicorn process/socket probe, Nginx change, VPS/systemd work or deployment. Preserve paper-first, `ai_execution_enabled=false`, and no-real-orders restrictions.
