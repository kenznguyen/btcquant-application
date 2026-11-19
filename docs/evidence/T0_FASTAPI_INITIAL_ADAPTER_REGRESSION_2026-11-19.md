# T0 FastAPI Migration — Initial ASGI Adapter and CI Evidence

- Date: 2026-11-19
- Repository: `kenznguyen/btcquant-application`
- Branch: `main`
- Latest paired source SHA: `f72cff4d78bbfe7beb1a3b3fe1dd6e03fe26a4f5`
- Scope: source-only FastAPI adapter and isolated GitHub Actions tests; no runtime/deployment work.

## 1. Work recorded

- Added `market_data/test_fastapi_api.py` with 10 ASGI contract tests.
- Added `market_data/fastapi_app.py`, a synchronous FastAPI route adapter for `GET /health` and `GET /v1/candles`. The route uses the existing Candle Contract 1.1.0 parser/freshness calculation and read-only storage factory.
- Disabled FastAPI docs/OpenAPI endpoints; all adapter responses set `Cache-Control: no-store`.
- Preserved explicit 400 invalid-query behavior rather than FastAPI's default 422; mapped 401, 404, 405/Allow and 503 behavior.
- Kept SQLite calls in synchronous route handlers. No acquisition, write, lease, initialization, migration or trading routes were added.
- Added separate runtime and ASGI-test dependency inputs:
  - `requirements-market-data-fastapi.in`: FastAPI 0.165.0, Uvicorn 0.54.0.
  - `requirements-market-data-fastapi-test.in`: runtime input plus httpx2 2.16.2.
- Added `.github/workflows/t0-fastapi-migration.yml`; it resolves separate exact-version, SHA-256 hashed runtime/test locks in CPython 3.12.16 and runs the ASGI contract tests.
- Updated the SQLite aggregate workflow path filter so FastAPI adapter changes trigger the existing 196-test regression.

## 2. Exact source commits

| Commit | Change |
|---|---|
| `9098524e02b33056bf323966862ae54619946d6d` | Add FastAPI contract tests before adapter |
| `b8380ee6fdb529d0533685472da4b1d604b1acdd` | Initial FastAPI dependency inputs |
| `1166467d115b99bdd82c511c97ca0118e4f0ea33` | Use Starlette-supported httpx2 test client |
| `13a141aca8234454dac4dd7bffaec80ba5f06e4b` | Pin FastAPI/Uvicorn runtime dependencies |
| `fbbdd06e79f0044129fa671442ddf8a00b4a30a6` | Separate ASGI test dependency input |
| `1564b9cf6d0857115530cb43b043e9cd899bae15` | Separate runtime/test hash-lock generation |
| `4be74b8e72a7f8cea554b37c1da327a228a3ad04` | Add read-only FastAPI adapter |
| `ffcf353e61b200f2bbfabbae7c5d6ed17584ea6c` | Run contract tests after adapter addition |
| `e73e9f37bbdaadec0a0c81cd3a4a8635d0c33616` | Pair FastAPI workflow with aggregate commit |
| `f72cff4d78bbfe7beb1a3b3fe1dd6e03fe26a4f5` | Trigger paired FastAPI and SQLite aggregate checks |

All commits are on the existing `main` branch. No branch/PR divergence was introduced.

## 3. TDD and dependency evidence

### Initial RED

- Run [44524571187](https://github.com/kenznguyen/btcquant-application/actions/runs/44524571187), exact SHA `1564b9cf6d0857115530cb43b043e9cd899bae15`.
- CPython 3.12.16 dependency resolution and hash-checked installation succeeded.
- Test discovery stopped at the expected missing `market_data.fastapi_app` import. This was a valid initial RED but did not execute the individual contract tests.
- Artifact ID: `14528773351`; artifact SHA-256: `41de1376dc542dab083bec4649e1f931e76e547e06d7a50f4cb52365fbcfcb7a`.
- Generated runtime lock SHA-256: `ed5d71e2796303e45266637dc0bffd980e9f869d9c1f25dc61abed8fffa2ee54`.
- Generated test lock SHA-256: `fe4b7109fb211671e90c26a8158b29d7b7d5be6cb0d8be3f9f4c150767bfd7ea`.

### FastAPI contract GREEN

- Run [44525016702](https://github.com/kenznguyen/btcquant-application/actions/runs/44525016702), job `135563357254`.
- Exact tested SHA: `f72cff4d78bbfe7beb1a3b3fe1dd6e03fe26a4f5`.
- CPython 3.12.16; **10/10 tests PASS**.
- Artifact ID: `14529288115`; artifact SHA-256: `6ca6bf9531af536d2cd140e7609934e3b876105c8bfcc4fb6ac74e7a49b4054b`.
- The artifact contains the generated runtime/test locks, SHA-256 records, Python version, installed package inventory and test log.
- Lock files are currently preserved in the CI artifact and are **not yet committed as repository lock files**. Their committed, reproducible installation gate remains a follow-up item.

### Existing SQLite regression on the same SHA

- Run [44525016662](https://github.com/kenznguyen/btcquant-application/actions/runs/44525016662), job `135563156844`.
- Exact tested SHA: `f72cff4d78bbfe7beb1a3b3fe1dd6e03fe26a4f5`.
- **196/196 PASS**.
- Artifact ID: `14529039136`; artifact SHA-256: `e4fe7e0bece4353b438c6a22cd7b2c36f27c88b2152fd2d9849b84a88388d09e`.

## 4. Intermediate CI correction

- An intermediate run on `13a141aca8234454dac4dd7bffaec80ba5f06e4b` failed because the test client dependency had not yet been separated/installed (`httpx2) required by Starlette 1.10.0).
- The dependency input was corrected to use `httpx2==2.16.2`, with runtime and test dependency inputs separated.
- The corrected run [44524571187](https://github.com/kenznguyen/btcquant-application/actions/runs/44524571187) verified dependency installation and the expected RED; the later 10-test GREEN runs verify the corrected setup.
- This intermediate failure is retained as evidence and was not hidden or overwritten.

## 5. Current boundary and remaining work

- FastAPI adapter: **IMPLEMENTED — 10/10 focused tests PASS**.
- Existing SQLite aggregate: **196/196 PASS on the same SHA**.
- Full WSGI-to-ASGI migration: **PARTIAL**. `market_data/api.py` still contains the WSGI application and `market_data/test_api.py` still exercises that entrypoint. The old WSGI path has not yet been removed.
- Full contract parity: **NOT YET VERIFIED**. The 10 new tests cover the initial adapter contract; the full existing API 1.1.0 test coverage must be ported to ASGI before WSGI removal.
- Runtime/test lock files: generated and hash-verified in the CI artifact; **not yet committed** as repository lock files.
- Independent code review: **PENDING**.
- Endpoint/runtime/VPS/Nginx/systemd/deployment: **NOT AUTHORIZED / NOT VERIFIED**.
- PostgreSQL/TimescaleDB: **PARKED**.
- T1/T2 connections: **NOT AUTHORIZED**.
- Canonical SQLite data/schema, writer/lease/feeder/recovery, retention and deletion: **UNCHANGED**.
- Live trading and real orders: **NOT AUTHORIZED**; `AI_EXECUTION_ENABLED=false`.
- Production readiness: **NOT CERTIFIED**.

## 6. Next bounded steps

1. Commit the exact generated runtime and test lock files (or regenerate them under a committed, reproducible lock process) and verify clean hash-based installation.
2. Port all existing `market_data/test_api.py` 1.1.0 contract cases to ASGI, including freshness/evaluability, sync/reopen, gap representation and timestamp provenance.
3. Run focused FastAPI tests and the 196-test SQLite aggregate on the exact same source SHA.
4. Remove the WSGI entrypoint and Gunicorn serving dependency only after full parity is green; rerun all relevant tests.
5. Obtain independent code review and record the exact reviewed SHA.
6. Request separate approval before any endpoint probe, Nginx routing, process startup, VPS or deployment work.

No runtime or cross-layer action is implied by the source-level PASS.
