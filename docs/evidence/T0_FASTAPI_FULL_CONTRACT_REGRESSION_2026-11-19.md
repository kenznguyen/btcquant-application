# T0 FastAPI — Full Candle Contract Regression Evidence

- Date: 2026-11-19
- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Exact paired source SHA: `a03637372e3090595bf6e48c9426e7e076cf3bdc`

## 1. Scope

This is a source-level contract test checkpoint for the initial FastAPI ASGI adapter. It does not qualify a running service, deployment or production operation.

## 2. Paired GitHub Actions evidence

| Suite | Run | Result | Job |
|---|---:|---:|---:|
| FastAPI ASGI Candle Contract | [44525859272](https://github.com/kenznguyen/btcquant-application/actions/runs/44525859272) | **25/25 PASS** | `135566117694` |
| Existing SQLite-only aggregate | [44525859257](https://github.com/kenznguyen/btcquant-application/actions/runs/44525859257) | **196/196 PASS** | `135566117671` |

Both workflows checked out exact SHA `a03637372e3090595bf6e48c9426e7e076cf3bdc`.

Artifacts:
- FastAPI: ID `14528454863`, SHA-256 `e6cafec6024a69cfa8fb2fbdfdb30eebfbd32214107455cee28934731b6d9196`.
- SQLite aggregate: ID `14531695273`, SHA-256 `5aefa96fd860f02a12a71f05f5db7a51c938676d7eff5d20cc3999405b169a6c`.

## 3. Contract coverage

The 25 ASGI tests cover:
- Public `GET /health`; read-only `GET /v1/candles`.
- Bearer authentication and missing/invalid configuration.
- Invalid, duplicate, unbounded and unknown query parameters; 400 rather than 422.
- 401, 404, 405 with `Allow: GET`, 503 and `Cache-Control: no-store`.
- BTCUSDT market identity, contract/schema versions, decimal OHLCV strings and dataset version.
- Half-open candle windows, gaps, persisted reads, closed-candle state, first-observed availability and quality provenance.
- `asOfMs` historical evaluation anchoring, future-anchor rejection and no backdating of imported data.
- Timestamp validity, freshness and evaluability, including complete, incomplete, stale and empty windows.
- Corrupt stored price rejection.
- Missing SQLite database non-creation and explicit PostgreSQL backend fail-closed behavior.
- Sync-to-reopened-API read behavior and observation-time preservation.
- Duplicate query parameter rejection and non-GET method rejection.

The existing 196-test SQLite aggregate was not weakened or expanded to PostgreSQL/runtime tests.

## 4. Dependency evidence

- CPython target: 3.12.16 / Linux x86_64.
- Runtime input: FastAPI 0.165.0 and Uvicorn 0.54.0.
- ASGI test input: runtime set plus httpx2 2.16.2.
- Resolved Starlette 1.10.0 and Pydantic 2.14.3.
- SHA-256 runtime lock: `ed5d71e2796303e45266637dc0bffd980e9f869d9c1f25dc61abed8fffa2ee54`.
- SHA-256 test lock: `fe4b7109fb211671e90c26a8158b29d7b7d5be6cb0d8be3f9f4c150767bfd7ea`.
- The generated lock files and their hash records are in the FastAPI CI artifact. They are not yet committed as repository lock files; committing and revalidating them remains open.

## 5. Current migration status

- FastAPI adapter source and focused ASGI tests: **PASS 25/25**.
- Existing SQLite regression: **PASS 196/196**, same exact source SHA.
- Initial WSGI-to-ASGI migration: **PARTIAL**. The old WSGI application in `market_data/api.py` and its tests in `market_data/test_api.py` remain in the repository.
- No claim is made that the WSGI entrypoint has been removed or that FastAPI has replaced it in any runtime.
- Independent code review: **PENDING**.
- Runtime/deployment: **NOT AUTHORIZED / NOT VERIFIED**.
- Production readiness: **NOT CERTIFIED**.

## 6. Next steps

1. Commit the exact dependency lock files and verify hash-based clean installation.
2. Perform independent code review of the FastAPI adapter, contract tests and workflow.
3. Only after review acceptance, plan the bounded removal of the WSGI entrypoint and Gunicorn serving dependency; retain the Candle Contract 1.1.0 behavior.
4. Re-run the 25 ASGI tests and 196 SQLite aggregate on one exact SHA after WSGI removal.
5. Request separate approval before endpoint probes, Nginx, VPS, systemd or deployment work.

No PostgreSQL qualification, T1/T2 connection, canonical database change, data retention/deletion change, live execution or real order was performed.
